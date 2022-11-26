import {
    derived,
    get,
    writable,
    type Readable,
    type Writable,
} from "svelte/store";

const HISTORY = 16;
const SERVER_URL = "ws://localhost:8080/ws";

const tx = new EventTarget();

export const connectionSwitch = writable<number | false>(false);

export enum ConnectionStatus {
    Connecting,
    Connected,
    Disconnected,
}

export function connect() {
    connectionSwitch.update((x) => x || 1);
}

export function reconnect() {
    connectionSwitch.update((x) => (x ? x + 1 : 1));
}

export function disconnect() {
    connectionSwitch.set(false);
}

export const socketUrl = writable(SERVER_URL);

const socket = derived<Writable<number | boolean>, WebSocket | null>(
    connectionSwitch,
    ($id, set) => {
        if (!$id) {
            set(null);
            return;
        }

        const ws = new WebSocket(get(socketUrl));

        const txHandler = (e: Event) => {
            if (e instanceof CustomEvent && ws?.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(e.detail));
            }
        };

        ws.addEventListener("open", () => {
            tx.addEventListener("message", txHandler);
        });

        set(ws);

        return () => {
            tx.removeEventListener("message", txHandler);
            ws?.close();
        };
    },
    null
);

export const connectionStatus = derived(
    socket,
    ($socket, set) => {
        if (!$socket) return set(ConnectionStatus.Disconnected);

        const openHandler = () => set(ConnectionStatus.Connected);
        const closeHandler = () => set(ConnectionStatus.Disconnected);

        switch ($socket.readyState) {
            case WebSocket.CONNECTING:
                set(ConnectionStatus.Connecting);
                $socket.addEventListener("open", openHandler);
                $socket.addEventListener("close", closeHandler);
                break;

            case WebSocket.OPEN:
                set(ConnectionStatus.Connected);
                $socket.addEventListener("close", closeHandler);
                break;

            default:
                set(ConnectionStatus.Disconnected);
                break;
        }

        return () => {
            $socket.removeEventListener("open", openHandler);
            $socket.removeEventListener("close", closeHandler);
        };
    },
    ConnectionStatus.Disconnected
);

export const events = derived<
    Readable<WebSocket | null>,
    { type: string; data: unknown } | null
>(
    socket,
    (ws, set) => {
        if (!ws) return;

        const handler = (e: MessageEvent) => {
            const payload = JSON.parse(e.data);
            set(payload);
        };

        ws.addEventListener("message", handler);

        return () => {
            ws.removeEventListener("message", handler);
        };
    },
    null
);

export const state = derived(
    socket,
    (ws, set) => {
        if (!ws) return;

        let msgs: unknown[] = [];
        let state: Record<string, unknown> = {};

        const handler = (e: MessageEvent) => {
            const { type, data } = JSON.parse(e.data);

            switch (type) {
                case "msg":
                    msgs = [data, ...msgs].slice(0, HISTORY);
                    break;

                case "state":
                    state = data as Record<string, unknown>;
                    break;

                case "patch":
                    state = { ...state, ...(data as Record<string, unknown>) };
                    break;
            }

            set({ msgs, state });
        };

        ws.addEventListener("message", handler);

        return () => {
            ws.removeEventListener("message", handler);
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
