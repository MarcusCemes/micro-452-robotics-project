<script lang="ts">
    import type { State } from "$lib/connection";
    import type { Scale } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import Dot from "./Dot.svelte";
    import Obstacles from "./Obstacles.svelte";
    import Path from "./Path.svelte";
    import Thymio from "./Thymio.svelte";

    export let nodes = false;
    export let scale: Scale;
    export let state: State;

    $: ({
        extra_obstacles: extraObstacles,
        obstacles,
        orientation,
        subdivisions,
    } = state);

    $: start = Vec2.tryParse(state.start);
    $: end = Vec2.tryParse(state.end);

    $: path = state.path
        ?.map((r) => Vec2.tryParse(r))
        .filter((x): x is Vec2 => !!x);

    $: position = Vec2.tryParse(state.position);
</script>

{#if extraObstacles && obstacles && subdivisions}
    <Obstacles {nodes} {extraObstacles} {obstacles} {scale} {subdivisions} />
{/if}

{#if path}
    <Path {path} {scale} />
{/if}

{#if start}
    <Dot class="bg-green-500" position={start} />
{/if}

{#if end}
    <Dot class="bg-red-500" position={end} />
{/if}

{#if position && orientation}
    <Thymio {position} {orientation} {scale} />
{/if}
