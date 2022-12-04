import { derived, writable, type Readable } from "svelte/store";
import { state } from "./connection";
import { Vec2 } from "./utils";

const DEFAULT_PHYSICAL_SIZE = 1;

export interface Scale {
    mapSize: Vec2;
    physicalSize: number;
}

export const mapSize = writable(new Vec2(256, 256));

export const scale: Readable<Scale> = derived(
    [state, mapSize],
    ([$state, $mapSize]) => ({
        physicalSize: $state?.physical_size || DEFAULT_PHYSICAL_SIZE,
        mapSize: $mapSize,
    })
);
