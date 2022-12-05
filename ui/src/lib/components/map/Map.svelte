<script lang="ts">
    import {
        ConnectionStatus,
        connectionStatus,
        send,
        state as stateStore,
    } from "$lib/connection";
    import { mapSize, scale as scaleStore } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import { cubicInOut } from "svelte/easing";
    import { fade } from "svelte/transition";
    import Actions from "./Actions.svelte";
    import MapView from "./MapView.svelte";
    import MouseInfo from "./MouseInfo.svelte";
    import Obstacle from "./Obstacle.svelte";

    let map: HTMLDivElement | null = null;
    let action: "position" | "end" | "obstacle" | null = null;

    let newObstacle: Vec2 | null = null;
    let mousePosition: Vec2 | null = null;

    let drawNodes = false;

    $: scale = $scaleStore;
    $: status = $connectionStatus;
    $: state = $stateStore;
    $: optimise = state?.optimise ?? false;

    $: disconnected = status !== ConnectionStatus.Connected;

    function clearObstacles() {
        send("clear_obstacles", null);
    }

    function onOptimise() {
        send("optimise", !optimise);
    }

    function onStop() {
        send("stop", null);
    }

    function onClick(event: MouseEvent) {
        const pos = getPosition(event).toPhysicalSpace(scale).array();

        switch (action) {
            case "position":
                send("set_position", pos);
                break;

            case "end":
                send("set_end", pos);
                break;

            case "obstacle":
                if (!newObstacle) {
                    newObstacle = getPosition(event);
                } else {
                    const end = getPosition(event);

                    const obstacle = [newObstacle, end].map((v) =>
                        v.toPhysicalSpace(scale).array()
                    );

                    send("add_obstacle", obstacle);
                    newObstacle = null;
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

    function onKeyDown(event: KeyboardEvent) {
        if (newObstacle && event.key === "Escape") {
            event.preventDefault();
            newObstacle = null;
        }
    }

    function onContextMenu(event: MouseEvent) {
        if (newObstacle) {
            event.preventDefault();
            newObstacle = null;
        }
    }

    function getPosition(event: MouseEvent) {
        const rect = map!.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        return new Vec2(x, y);
    }
</script>

<svelte:window on:keydown={onKeyDown} />

<Actions
    bind:action
    bind:drawNodes
    {optimise}
    on:clear={clearObstacles}
    on:optimise={onOptimise}
    on:stop={onStop}
/>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
    bind:this={map}
    on:click={onClick}
    on:mousemove={onMouseMove}
    on:mouseleave={onMouseLeave}
    on:contextmenu={onContextMenu}
    bind:clientWidth={$mapSize.x}
    bind:clientHeight={$mapSize.y}
    class="relative w-96 h-96 bg-white ring-1 ring-gray-200 overflow-hidden shadow-2xl transition"
    class:ring-gray-300={!disconnected}
>
    {#if state}
        <MapView {drawNodes} {scale} {state} />

        {#if newObstacle && mousePosition}
            <div class="opacity-50">
                <Obstacle from={newObstacle} to={mousePosition} screenSpace />
            </div>
        {/if}
    {/if}

    {#if disconnected || !state}
        <div
            transition:fade={{ duration: 200, easing: cubicInOut }}
            class="absolute inset-0 flex flex-col justify-center items-center bg-white bg-opacity-50 font-bold select-none backdrop-blur-sm"
        >
            {#if disconnected}
                <div class="text-2xl">📵</div>
                <div class="mb-2 text-sm">Disconnected</div>
            {:else}
                <div class="text-2xl">🚀</div>
                <div class="mb-2 text-sm">Waiting for state...</div>
            {/if}
        </div>
    {/if}
</div>

{#if state?.subdivisions}
    <MouseInfo {mousePosition} subdivisions={state.subdivisions} {scale} />
{/if}
