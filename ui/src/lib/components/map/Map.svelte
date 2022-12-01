<script lang="ts">
    import { send, state } from "$lib/connection";
    import { mapSize, scale } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import Dot from "./Dot.svelte";
    import IconButton from "./IconButton.svelte";
    import Obstacle from "./Obstacle.svelte";
    import Thymio from "./Thymio.svelte";

    let map: HTMLDivElement;
    let canvas: HTMLCanvasElement;
    let action: "start" | "end" | "obstacle" | null = null;

    let obstacleStart: Vec2 | null = null;
    let mousePosition: Vec2 | null = null;

    $: e = $state;
    $: console.log(e);

    $: start = Vec2.parse(e.state.start);
    $: end = Vec2.parse(e.state.end);
    $: subdivisions = (e.state.subdivisions as number | undefined) || 64;

    $: position = Vec2.parse(e.state.position);
    $: orientation = e.state.orientation as number | undefined;

    $: path = e.state.path as [number, number][] | undefined;

    $: physicalMousePosition = mousePosition?.toPhysicalSpace($scale);

    $: coordinateMousePosition = physicalMousePosition?.multiplyBy(
        new Vec2(
            subdivisions / $scale.physicalSize.x,
            subdivisions / $scale.physicalSize.y
        )
    );

    $: pathPoints = path
        ?.map((r) => {
            const v = Vec2.parse(r)?.toScreenSpace($scale);
            return v && `${v.x} ${v.y}`;
        })
        .filter((x) => !!x)
        .join(",");

    $: obstacles = e.state.obstacles as [number, number][] | undefined;
    $: if (obstacles) drawObstacles(obstacles, canvas);

    $: extraObstacles = e.state.extra_obstacles as
        | [[number, number], [number, number]][]
        | undefined;

    $: extraObstacleVectors =
        extraObstacles?.map(([a, b]) => [Vec2.parse(a), Vec2.parse(b)]) ?? [];

    function drawObstacles(obstacles: number[][], canvas?: HTMLCanvasElement) {
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const subdivisions =
            ($state.state.subdivisions as number | undefined) || 64;

        ctx.save();
        ctx.fillStyle = "black";

        ctx.scale(
            $scale.mapSize.x / subdivisions,
            $scale.mapSize.y / subdivisions
        );

        for (let x = 0; x < obstacles.length; x++) {
            const row = obstacles[x];
            for (let y = 0; y < row.length; y++) {
                const mappedY = row.length - y - 1;
                if (row[y] === 1) {
                    ctx.fillRect(x, mappedY, 1, 1);
                }
            }
        }

        ctx.restore();
    }

    function clearObstacles() {
        send("clear_obstacles", null);
    }

    function onClick(event: MouseEvent) {
        const pos = getPosition(event).toPhysicalSpace($scale).array();

        switch (action) {
            case "start":
                send("set_start", pos);
                break;

            case "end":
                send("set_end", pos);
                break;

            case "obstacle":
                if (!obstacleStart) {
                    obstacleStart = getPosition(event);
                } else {
                    const end = getPosition(event);

                    const obstacle = [obstacleStart, end].map((v) =>
                        v.toPhysicalSpace($scale).array()
                    );

                    send("add_obstacle", obstacle);
                    obstacleStart = null;
                }
                break;
        }
    }

    function onMouseMove(event: MouseEvent) {
        mousePosition = getPosition(event);
    }

    function onMouseLeave() {
        mousePosition = null;
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

    function formatNumber(n?: number | null, digits: number = 2, padding = 4) {
        return n ? n.toFixed(digits).padStart(padding) : "-".padStart(padding);
    }
</script>

<div class="mb-2">
    <IconButton on:click={() => (action = "start")} active={action === "start"}>
        <span class="w-2 h-2 rounded-full bg-green-500" />
    </IconButton>
    <IconButton on:click={() => (action = "end")} active={action === "end"}>
        <span class="w-2 h-2 rounded-full bg-red-500" />
    </IconButton>
    <IconButton
        on:click={() => (action = "obstacle")}
        active={action === "obstacle"}
    >
        <span class="w-2 h-2 bg-black" />
    </IconButton>
    <IconButton on:click={clearObstacles}>🗑️</IconButton>
</div>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
    bind:this={map}
    on:click={onClick}
    on:contextmenu={onContextMenu}
    on:mousemove={onMouseMove}
    on:mouseleave={onMouseLeave}
    bind:clientWidth={$mapSize.x}
    bind:clientHeight={$mapSize.y}
    class="relative w-96 h-96 border border-gray-300 rounded bg-white"
>
    <canvas
        bind:this={canvas}
        width={$mapSize.x}
        height={$mapSize.y}
        class="absolute top-0 left-0"
    />

    {#each extraObstacleVectors as [from, to]}
        {#if from && to}
            <Obstacle {from} {to} />
        {/if}
    {/each}

    {#if obstacleStart && mousePosition}
        <div class="opacity-50">
            <Obstacle from={obstacleStart} to={mousePosition} screenSpace />
        </div>
    {/if}

    {#if pathPoints}
        <svg
            viewBox={`0 0 ${$mapSize.x} ${$mapSize.y}`}
            width={$mapSize.x}
            height={$mapSize.y}
            xmlns="http://www.w3.org/2000/svg"
            class="absolute top-0 left-0 text-teal-500"
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

<div>
    <div>
        x: {formatNumber(physicalMousePosition?.x)}cm - y: {formatNumber(
            physicalMousePosition?.y
        )}cm
    </div>
    <div>
        i: {formatNumber(coordinateMousePosition?.x, 0)} - j: {formatNumber(
            coordinateMousePosition?.y,
            0
        )}
    </div>
</div>
