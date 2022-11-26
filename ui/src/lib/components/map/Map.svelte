<script lang="ts">
    import { send, state } from "$lib/connection";
    import { mapSize, scale } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import Dot from "./Dot.svelte";
    import Obstacle from "./Obstacle.svelte";
    import Thymio from "./Thymio.svelte";

    let map: HTMLDivElement;

    let mouseDownStart = new Vec2(0, 0);

    $: e = $state;

    $: start = Vec2.parse(e.state.start);
    $: end = Vec2.parse(e.state.end);

    $: position = Vec2.parse(e.state.position);
    $: orientation = e.state.orientation as number | undefined;

    $: path = e.state.path as [number, number][] | undefined;
    $: console.log(path);
    $: pathPoints = path
        ?.map((r) => {
            const v = Vec2.parse(r)?.toScreenSpace($scale);
            return v && `${v.x} ${v.y}`;
        })
        .filter((x) => !!x)
        .join(",");

    $: obstacles = e.state.obstacles as
        | [[number, number], [number, number]][]
        | undefined;

    $: obstacleVectors =
        obstacles?.map(([a, b]) => [Vec2.parse(a), Vec2.parse(b)]) ?? [];

    function onClick(event: MouseEvent) {
        const pos = getPosition(event).toPhysicalSpace($scale).array();
        send("set_start", pos);
    }

    function onMouseDown(event: MouseEvent) {
        if (event.button !== 2) return;
        mouseDownStart = getPosition(event);
    }

    function onMouseUp(event: MouseEvent) {
        if (event.button !== 2) return;
        const end = getPosition(event);

        const normalised = normaliseObstacle(mouseDownStart, end);
        const obstacle = normalised.map((v) =>
            v.toPhysicalSpace($scale).array()
        );

        send("add_obstacle", obstacle);
    }

    function normaliseObstacle(a: Vec2, b: Vec2) {
        return [
            new Vec2(Math.min(a.x, b.x), Math.min(a.y, b.y)),
            new Vec2(Math.max(a.x, b.x), Math.max(a.y, b.y)),
        ];
    }

    function onContextMenu(event: MouseEvent) {
        event.preventDefault();
    }

    function getPosition(event: MouseEvent) {
        const rect = map.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        return new Vec2(x, y);
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
    bind:this={map}
    on:click={onClick}
    on:mousedown={onMouseDown}
    on:mouseup={onMouseUp}
    on:contextmenu={onContextMenu}
    bind:clientWidth={$mapSize.x}
    bind:clientHeight={$mapSize.y}
    class="relative w-96 h-96 border border-gray-300 rounded bg-white"
>
    {#each obstacleVectors as [from, to]}
        {#if from && to}
            <Obstacle {from} {to} />
        {/if}
    {/each}

    {#if pathPoints}
        <svg
            viewBox={`0 0 ${$mapSize.x} ${$mapSize.y}`}
            width={$mapSize.x}
            height={$mapSize.y}
            xmlns="http://www.w3.org/2000/svg"
            class="text-teal-500"
        >
            <polyline
                points={pathPoints}
                stroke="currentColor"
                fill="none"
                stroke-width="0.2em"
                stroke-linejoin="miter"
            />
        </svg>
    {/if}

    {#if start}
        <Dot class="bg-green-500" r={start} />
    {/if}

    {#if end}
        <Dot class="bg-red-500" r={end} />
    {/if}

    {#if position && orientation}
        <Thymio {position} {orientation} />
    {/if}
</div>
