import { derived, readable } from "svelte/store";

let ws: WebSocket | null = null;

const HISTORY = 16;
const SERVER_URL = "ws://localhost:8080/ws";

const tx = new EventTarget();

const socket = readable<WebSocket | null>(null, (set) => {
    ws = new WebSocket(SERVER_URL);

    const handler = (e: Event) => {
        if (e instanceof CustomEvent) ws?.send(JSON.stringify(e.detail));
    };

    ws.onopen = () => {
        tx.addEventListener("message", handler);
        set(ws);
    };

    return () => {
        tx.removeEventListener("message", handler);
        if (ws) ws.close();
    };
});

export const events = derived(
    socket,
    (ws, set) => {
        if (!ws) return;

        let msgs: unknown[] = [];
        let state = {};

        ws.onmessage = (e) => {
            const msg = JSON.parse(e.data);

            switch (msg.type) {
                case "msg":
                    msgs = [msg.data, ...msgs].slice(0, HISTORY);
                    break;

                case "state":
                    state = msg.data;
                    break;

                case "patch":
                    state = { ...state, ...msg.data };
                    break;
            }

            set({ msgs, state });
        };
    },
    { msgs: [], state: {} } as {
        msgs: unknown[];
        state: Record<string, unknown>;
    }
);

export function send(type: string, data: unknown) {
    tx.dispatchEvent(new CustomEvent("message", { detail: { type, data } }));
}
