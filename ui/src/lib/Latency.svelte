<script lang="ts">
    import { nanoid } from "nanoid";
    import { SmoothieChart, TimeSeries } from "smoothie";
    import { onMount } from "svelte";
    import type { Unsubscriber } from "svelte/store";
    import { events, send } from "./connection";

    const smoothie = new SmoothieChart();
    const latency = new TimeSeries();

    smoothie.addTimeSeries(latency);

    let enabled = false;
    let chart: HTMLCanvasElement;
    let interval = 10;

    let id = "";
    let sentAt = performance.now();
    let unsubscribe: Unsubscriber | null = null;

    $: if (enabled) {
        receivePings();
        queuePing();
    } else if (unsubscribe) {
        unsubscribe();
        unsubscribe = null;
    }

    onMount(() => {
        smoothie.streamTo(chart);
    });

    function queuePing() {
        id = nanoid();
        sentAt = performance.now();
        send("ping", id);
    }

    function receivePings() {
        unsubscribe = events.subscribe((event) => {
            if (!event) return;
            if (event.type === "pong" && event.data === id) {
                const end = performance.now();
                latency.append(Date.now(), end - sentAt);

                setTimeout(() => {
                    if (enabled) {
                        queuePing();
                    }
                }, interval);
            }
        });
    }

    function onClick() {
        enabled = !enabled;
    }
</script>

<button on:click={onClick} class="px-2 py-1 border rounded">
    {#if enabled}
        Stop
    {:else}
        Start
    {/if}
</button>

{#if enabled}
    <span class="font-bold">Interval</span>
    <input
        bind:value={interval}
        class="px-2 py-1 border"
        type="number"
        min="0"
        max="1000"
    />
{/if}

<canvas
    bind:this={chart}
    width="300"
    height="100"
    class="my-2"
    class:hidden={!enabled}
/>
