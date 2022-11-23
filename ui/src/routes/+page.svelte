<script lang="ts">
    import {
        connect,
        connected,
        disconnect,
        reconnect,
        state,
    } from "$lib/connection";
    import Latency from "$lib/Latency.svelte";
    import Map from "$lib/Map.svelte";

    $: e = $state;

    $: time = e.state.computation_time as number | undefined;
</script>

<div class="min-h-screen grid grid-cols-5">
    <div class="px-6 py-3 col-span-2 border-r">
        {#if $connected}
            <span class="text-green-500 font-bold text-lg">Connected</span>
        {:else}
            <span class="text-red-500 font-bold text-lg">Disconnected</span>
        {/if}

        <div>
            <button on:click={connect} class="px-2 py-1 border">Connect</button>
            <button on:click={reconnect} class="px-2 py-1 border"
                >Reconnect</button
            >
            <button on:click={disconnect} class="px-2 py-1 border"
                >Disconnect</button
            >
        </div>

        <h2 class="mb-2 text-lg font-bold">Latency</h2>
        <Latency />

        <h2 class="mb-2 text-lg font-bold">Messages</h2>

        <div>
            {#each e.msgs as msg}
                <div class="my-1 p-2 border overflow-x-auto rounded">
                    <pre>{JSON.stringify(msg)}</pre>
                </div>
            {/each}
        </div>

        {#if time}
            <div class="mt-2">
                Computation time: {Math.round(time * 1000)} ms
            </div>
        {/if}
    </div>

    <div class="col-span-3 flex justify-center items-center bg-gray-50">
        <Map />
    </div>
</div>
