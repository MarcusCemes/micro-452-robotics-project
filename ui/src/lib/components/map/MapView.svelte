<script lang="ts">
    import type { State } from "$lib/connection";
    import type { Scale } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import Dot from "./Dot.svelte";
    import Obstacles from "./Obstacles.svelte";
    import Path from "./Path.svelte";
    import Thymio from "./Thymio.svelte";
    import Detect from "./Detect.svelte";

    export let drawNodes = false;
    export let scale: Scale;
    export let state: State;

    $: ({
        boundary_map: boundaryMap,
        extra_obstacles: extraObstacles,
        last_detection: lastDetection,
        last_detection_front: lastDetectionFront,
        last_orientation: lastOrientation,
        obstacles,
        orientation,
        next_waypoint_index,
        nodes,
        subdivisions,
    } = state);

    $: end = Vec2.tryParse(state.end);

    $: path = state.path
        ?.map((r) => Vec2.tryParse(r))
        .filter((x): x is Vec2 => !!x);

    $: position = Vec2.tryParse(state.position);

    $: next_waypoint =
        typeof next_waypoint_index === "number" &&
        path &&
        path.length > next_waypoint_index
            ? path[next_waypoint_index]
            : null;

    $: detectDot = Vec2.tryParse(lastDetection);
    $: detectFrontDot = Vec2.tryParse(lastDetectionFront);
</script>

{#if extraObstacles && obstacles && subdivisions}
    <Obstacles
        {drawNodes}
        {boundaryMap}
        {extraObstacles}
        {nodes}
        {obstacles}
        {scale}
        {subdivisions}
    />
{/if}

{#if path}
    <Path {path} {scale} />
{/if}

{#if end}
    <Dot class="bg-red-500" position={end} />
{/if}

{#if next_waypoint}
    <Dot class="bg-green-500" position={next_waypoint} small ping />
{/if}

{#if position && typeof orientation === "number"}
    <Thymio {position} {orientation} {scale} />
{/if}

{#if detectDot && typeof lastOrientation === "number"}
    <Detect position={detectDot} orientation={lastOrientation} {scale} />
{/if}

{#if detectDot}
    <Dot class="bg-pink-500" position={detectDot} small ping />
{/if}

{#if detectFrontDot}
    <Dot class="bg-blue-600" position={detectFrontDot} small ping />
{/if}
