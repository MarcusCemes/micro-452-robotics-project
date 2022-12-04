<script lang="ts">
    import type { State } from "$lib/connection";
    import type { Scale } from "$lib/stores";
    import { ObstacleRenderer } from "./obstacle_renderer";

    export let boundaryMap: State["boundary_map"];
    export let drawNodes: boolean;
    export let extraObstacles: State["extra_obstacles"];
    export let nodes: State["nodes"];
    export let obstacles: State["obstacles"];
    export let scale: Scale;
    export let subdivisions: number;

    let canvas: HTMLCanvasElement | null = null;

    $: ({ x: width, y: height } = scale.mapSize);

    $: renderer = canvas && new ObstacleRenderer(canvas, scale, subdivisions);

    $: {
        if (renderer) {
            renderer.drawObstacles(obstacles, extraObstacles);

            if (drawNodes) {
                renderer.drawNodes(
                    obstacles,
                    extraObstacles,
                    boundaryMap,
                    scale,
                    nodes
                );
            }
        }
    }
</script>

<canvas bind:this={canvas} class="absolute top-0 left-0" {width} {height} />
