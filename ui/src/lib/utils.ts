import type { Scale } from "./stores";

export class Vec2 {
    constructor(public x: number, public y: number) {}

    add(rhs: Vec2): Vec2 {
        return new Vec2(this.x + rhs.x, this.y + rhs.y);
    }

    multiply(scalar: number): Vec2 {
        return new Vec2(this.x * scalar, this.y * scalar);
    }

    multiplyBy(rhs: Vec2): Vec2 {
        return new Vec2(this.x * rhs.x, this.y * rhs.y);
    }

    divide(scalar: number): Vec2 {
        return new Vec2(this.x / scalar, this.y / scalar);
    }

    divideBy(rhs: Vec2): Vec2 {
        return new Vec2(this.x / rhs.x, this.y / rhs.y);
    }

    eq(rhs: Vec2): boolean {
        return this.x === rhs.x && this.y === rhs.y;
    }

    sub(rhs: Vec2): Vec2 {
        return new Vec2(this.x - rhs.x, this.y - rhs.y);
    }

    floor(): Vec2 {
        return new Vec2(Math.floor(this.x), Math.floor(this.y));
    }

    toScreenSpace(scale: Scale, invertY = true): Vec2 {
        const r = this.divideBy(scale.physicalSize).multiplyBy(scale.mapSize);
        if (invertY) r.y = scale.mapSize.y - r.y;
        return r;
    }

    toPhysicalSpace(scale: Scale, invertY = true): Vec2 {
        const r = this.divideBy(scale.mapSize).multiplyBy(scale.physicalSize);
        if (invertY) r.y = scale.physicalSize.y - r.y;
        return r;
    }

    array(): [number, number] {
        return [this.x, this.y];
    }

    static parse(coords?: unknown): Vec2 | undefined {
        if (coords instanceof Array && coords.length >= 2)
            return new Vec2(coords[0], coords[1]);
    }
}

export type ClassValue =
    | string
    | null
    | undefined
    | false
    | { [index: string]: boolean };

/** A custom implementation of the `classnames`/`clsx` library. */
export function classes(...classes: ClassValue[]): string {
    return classes
        .flatMap(expandObjects)
        .filter((x) => !!x)
        .join(" ");
}

function expandObjects(x: ClassValue) {
    if (isObject(x)) {
        return Object.entries(x).map(([key, value]) =>
            value ? key : undefined
        );
    } else {
        return x;
    }
}

function isObject(x: unknown): x is { [index: string]: unknown } {
    return typeof x === "object" && x !== null;
}
