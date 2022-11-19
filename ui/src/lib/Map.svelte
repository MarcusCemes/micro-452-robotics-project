<script lang="ts">
    import { events, send } from "./connection";
    import Dot from "./Dot.svelte";
    import Obstacle from "./Obstacle.svelte";
    import { app } from "./stores";
    import { Vec2 } from "./utils";

    let map: HTMLDivElement;

    let mouseDownStart = new Vec2(0, 0);

    $: e = $events;

    $: physicalSize = e.state.size as number | undefined;
    $: updatePhysicalSize(physicalSize);

    $: start = Vec2.parse(e.state.start);
    $: end = Vec2.parse(e.state.end);
    $: pos = Vec2.parse(e.state.pos);

    $: path = e.state.path as [number, number][] | undefined;
    $: pathDots = path?.map(Vec2.parse) ?? [];

    $: obstacles = e.state.obstacles as
        | [[number, number], [number, number]][]
        | undefined;

    $: obstacleVectors =
        obstacles?.map(([a, b]) => [Vec2.parse(a), Vec2.parse(b)]) ?? [];

    function updatePhysicalSize(size: number | undefined) {
        if (size) $app.physicalSize = new Vec2(size, size);
    }

    function onClick(event: MouseEvent) {
        const pos = getPosition(event).toPhysicalSpace($app).array();
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
        const obstacle = normalised.map((v) => v.toPhysicalSpace($app).array());

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
    bind:clientWidth={$app.mapSize.x}
    bind:clientHeight={$app.mapSize.y}
    class="relative w-96 h-96 border border-gray-300 rounded bg-white"
>
    {#each obstacleVectors as [from, to]}
        {#if from && to}
            <Obstacle {from} {to} />
        {/if}
    {/each}

    {#each pathDots as r}
        {#if r}
            <Dot class="bg-yellow-500 scale-50" {r} />
        {/if}
    {/each}

    {#if start}
        <Dot class="bg-green-500" r={start} />
    {/if}

    {#if end}
        <Dot class="bg-red-500" r={end} />
    {/if}

    {#if pos}
        <Dot class="bg-blue-400" ping r={pos} />
    {/if}
</div>
