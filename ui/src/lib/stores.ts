import { derived, writable, type Readable } from "svelte/store";
import { state } from "./connection";
import { Vec2 } from "./utils";

const PHYSICAL_SIZE = 1;

export interface Scale {
    mapSize: Vec2;
    physicalSize: Vec2;
}

export const mapSize = writable(new Vec2(256, 256));

export const scale: Readable<Scale> = derived(
    [state, mapSize],
    ([$state, mapSize]) => {
        const s = $state.state.physical_size as [number, number] | undefined;

        const physicalSize = s
            ? new Vec2(s[0], s[1])
            : new Vec2(PHYSICAL_SIZE, PHYSICAL_SIZE);

        return { physicalSize, mapSize };
    }
);
