import {
    derived,
    get,
    writable,
    type Readable,
    type Writable,
} from "svelte/store";

/* == Constants == */

const HISTORY = 16;
const SERVER_URL = "ws://localhost:8080/ws";

/* == Types == */

export type Tuple2<T = number> = [T, T];
export type ExtraObstacle = Tuple2<Tuple2>;

export interface State {
    position: Tuple2 | null;
    orientation: number | null;

    start: Tuple2 | null;
    end: Tuple2 | null;

    path: Tuple2[] | null;
    next_waypoint_index: number | null;
    obstacles: number[][];
    extra_obstacles: ExtraObstacle[];
    boundary_map: number[][] | null;
    computation_time: number | null;

    subdivisions: number;
    physical_size: number;

    prox_sensors: number[];
    relative_distances: number[];
    reactive_control: boolean | null;
}

/* == Connection Status == */

export const connectionSwitch = writable<number | false>(false);

export enum ConnectionStatus {
    Connecting,
    Connected,
    Disconnected,
    Failed,
}

/* == Functions == */

const tx = new EventTarget();

export function connect() {
    connectionSwitch.update((x) => x || 1);
}

export function reconnect() {
    connectionSwitch.update((x) => (x ? x + 1 : 1));
}

export function disconnect() {
    connectionSwitch.set(false);
}

export function send(type: string, data: unknown) {
    tx.dispatchEvent(new CustomEvent("message", { detail: { type, data } }));
}

/* == Stores == */

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

        const errorHandler = () => {
            $socket.removeEventListener("close", closeHandler);
            set(ConnectionStatus.Failed);
        };

        switch ($socket.readyState) {
            case WebSocket.CONNECTING:
                set(ConnectionStatus.Connecting);
                $socket.addEventListener("open", openHandler);
                $socket.addEventListener("close", closeHandler);
                $socket.addEventListener("error", errorHandler);
                break;

            case WebSocket.OPEN:
                set(ConnectionStatus.Connected);
                $socket.addEventListener("close", closeHandler);
                $socket.addEventListener("error", errorHandler);
                break;

            default:
                set(ConnectionStatus.Disconnected);
                break;
        }

        return () => {
            $socket.removeEventListener("open", openHandler);
            $socket.removeEventListener("close", closeHandler);
            $socket.addEventListener("error", errorHandler);
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

export const server = derived(
    socket,
    (ws, set) => {
        if (!ws) return;

        let msgs: unknown[] = [];
        let state: State | null = null;

        const handler = (e: MessageEvent) => {
            const { type, data } = JSON.parse(e.data);

            switch (type) {
                case "msg":
                    msgs = [data, ...msgs].slice(0, HISTORY);
                    break;

                case "state":
                    state = data as State;
                    break;

                case "patch":
                    if (!state) {
                        console.error("Received patch before state!");
                        return;
                    }

                    state = {
                        ...state,
                        ...(data as Partial<State>),
                    };

                    break;
            }

            set({ msgs, state });
        };

        ws.addEventListener("message", handler);

        return () => {
            ws.removeEventListener("message", handler);
        };
    },
    { msgs: [], state: null } as {
        msgs: unknown[];
        state: State | null;
    }
);

export const state = derived(server, ($server) => $server.state, null);
