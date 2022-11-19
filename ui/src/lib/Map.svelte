<script lang="ts">
    import { events } from "./connection";
    import Dot from "./Dot.svelte";
    import { Vec2 } from "./utils";

    const SUBDIVISIONS = 16;

    let size = new Vec2(0, 0);

    $: e = $events;
    $: console.log(e.state);

    $: start = Vec2.parse(e.state.start)?.divide(SUBDIVISIONS);
    $: end = Vec2.parse(e.state.end)?.divide(SUBDIVISIONS);
    $: pos = Vec2.parse(e.state.pos)?.divide(SUBDIVISIONS);

    $: path = e.state.path as [number, number][] | undefined;
    $: pathDots =
        path?.map(Vec2.parse).map((v) => v?.divide(SUBDIVISIONS)) ?? [];
</script>

<div
    bind:clientWidth={size.x}
    bind:clientHeight={size.y}
    class="relative w-96 h-96 border border-gray-300 rounded bg-white"
>
    <Dot class="bg-black" r={{ x: 0.5, y: 0.5 }} {size} />

    {#each pathDots as r}
        <Dot class="bg-yellow-500 scale-50" {r} {size} />
    {/each}

    {#if start}
        <Dot class="bg-green-500" r={start} {size} />
    {/if}

    {#if end}
        <Dot class="bg-red-500" r={end} {size} />
    {/if}

    {#if pos}
        <Dot class="bg-blue-400" ping r={pos} {size} />
    {/if}
</div>
