import { derived, writable, type Readable } from "svelte/store";
import { state } from "./connection";
import { Vec2 } from "./utils";

const DEFAULT_PHYSICAL_SIZE = 1;

export interface Scale {
    mapSize: Vec2;
    physicalSize: Vec2;
}

export const mapSize = writable(new Vec2(256, 256));

export const scale: Readable<Scale> = derived(
    [state, mapSize],
    ([$state, $mapSize]) => {
        const size = $state?.physical_size;

        const physicalSize = size
            ? new Vec2(...size)
            : new Vec2(DEFAULT_PHYSICAL_SIZE, DEFAULT_PHYSICAL_SIZE);

        return { physicalSize, mapSize: $mapSize };
    }
);
