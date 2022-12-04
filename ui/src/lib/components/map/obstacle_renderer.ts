import type { ExtraObstacle, State } from "$lib/connection";
import type { Scale } from "$lib/stores";
import { Vec2 } from "$lib/utils";

const NODE_COLOUR = "#22c55e";
const NODE_COLOUR_BOUNDARY = "#f97316";
const NODE_COLOUR_OBSTACLE = "#ef4444";
const NODE_RADIUS = 1.5;
const TWO_PI = Math.PI * 2;

export class ObstacleRenderer {
    private ctx: CanvasRenderingContext2D;

    constructor(
        private readonly canvas: HTMLCanvasElement,
        private readonly scale: Scale,
        private readonly subdivisions: number
    ) {
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("Failed to get canvas context");

        this.ctx = ctx;
    }

    public drawObstacles(
        obstacles: State["obstacles"],
        extraObstacles: State["extra_obstacles"]
    ) {
        this.clear();
        this.ctx.save();

        const step = this.size();
        const size = step.mapEach(Math.ceil);

        this.ctx.fillStyle = "black";

        for (const coords of this.coordinates()) {
            if (obstacles.at(-coords.y - 1)?.at(coords.x) === 1) {
                const pos = coords.multiplyBy(step).mapEach(Math.floor);
                this.ctx.fillRect(pos.x, pos.y, size.x, size.y);
            }
        }

        for (const [startPhy, endPhy] of extraObstacles) {
            const from = Vec2.tryParse(startPhy)?.toScreenSpace(this.scale);
            const to = Vec2.tryParse(endPhy)?.toScreenSpace(this.scale);

            if (!from || !to) continue;

            const pos = new Vec2(
                Math.min(from.x, to.x),
                Math.min(from.y, to.y)
            ).mapEach(Math.floor);

            const size = to.sub(from).mapEach(Math.abs).mapEach(Math.ceil);
            this.ctx.fillRect(pos.x, pos.y, size.x, size.y);
        }

        this.ctx.restore();
    }

    public drawNodes(
        obstacles: State["obstacles"],
        extraObstacles: State["extra_obstacles"],
        boundaryMap: State["boundary_map"],
        scale: Scale
    ) {
        this.ctx.save();

        const step = this.size();
        const offset = new Vec2(0.5, 0.5);

        const colour = new NodeColour(
            obstacles,
            extraObstacles,
            boundaryMap,
            scale
        );

        for (const coords of this.coordinates()) {
            const pos = coords.add(offset).multiplyBy(step);

            this.ctx.fillStyle = colour.get(coords);
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, NODE_RADIUS, 0, TWO_PI);
            this.ctx.fill();
        }

        this.ctx.restore();
    }

    private nodeColour(
        coords: Vec2,
        position: Vec2,
        obstacles: State["obstacles"],
        extraObstacles: State["extra_obstacles"]
    ) {
        if (this.isObstructed(coords, position, obstacles, extraObstacles))
            return NODE_COLOUR_OBSTACLE;
        else if (this.isInBoundary(coords, position, obstacles, extraObstacles))
            return NODE_COLOUR_BOUNDARY;
        else return NODE_COLOUR;
    }

    private isInBoundary(
        coords: Vec2,
        position: Vec2,
        obstacles: State["obstacles"],
        extraObstacles: State["extra_obstacles"]
    ) {
        return (
            coords.x === 0 ||
            coords.y === 0 ||
            coords.x === this.subdivisions - 1 ||
            coords.y === this.subdivisions - 1 ||
            this.isObstructed(coords, position, obstacles, extraObstacles)
        );
    }

    private isObstructed(
        coords: Vec2,
        position: Vec2,
        obstacles: State["obstacles"],
        extraObstacles: State["extra_obstacles"]
    ): boolean {
        return (
            obstacles.at(-coords.y - 1)?.at(coords.x) === 1 ||
            extraObstacles.some(
                ([[x1, y1], [x2, y2]]) =>
                    within(position.x, x1, x2) && within(position.y, y1, y2)
            )
        );
    }

    private *coordinates() {
        for (let i = 0; i < this.subdivisions; i++) {
            for (let j = 0; j < this.subdivisions; j++) {
                yield new Vec2(i, j);
            }
        }
    }

    private size(): Vec2 {
        const width = this.canvas.width;
        const height = this.canvas.height;
        return new Vec2(width, height).divide(this.subdivisions);
    }

    private clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

class NodeColour {
    constructor(
        private readonly obstacles: State["obstacles"],
        private readonly extraObstacles: State["extra_obstacles"],
        private readonly boundaryMap: State["boundary_map"],
        private readonly scale: Scale
    ) {}

    public get(coords: Vec2) {
        const pos = coords.toPhysicalSpace(this.scale);

        if (this.isObstructed(coords, pos)) return NODE_COLOUR_OBSTACLE;
        else if (this.isInBoundary(coords)) return NODE_COLOUR_BOUNDARY;
        else return NODE_COLOUR;
    }

    private isInBoundary(coords: Vec2) {
        return this.boundaryMap && this.obstacle(coords, this.boundaryMap);
    }

    private isObstructed(coords: Vec2, position: Vec2) {
        return (
            this.obstacle(coords) ||
            this.extraObstacles.some((o) => this.inExtraObstacle(position, o))
        );
    }

    private inExtraObstacle(position: Vec2, obstacle: ExtraObstacle) {
        const [[x1, y1], [x2, y2]] = obstacle;
        return within(position.x, x1, x2) && within(position.y, y1, y2);
    }

    private obstacle(coords: Vec2, map = this.obstacles) {
        return map.at(-coords.y - 1)?.at(coords.x) !== 0;
    }
}

function within(x: number, a: number, b: number) {
    return x >= min(a, b) && x <= max(a, b);
}

function min(a: number, b: number) {
    return a > b ? b : a;
}

function max(a: number, b: number) {
    return a > b ? a : b;
}
