<script lang="ts">
    import {
        ConnectionStatus,
        connectionStatus,
        connectionSwitch,
    } from "$lib/connection";

    $: status = $connectionStatus;

    $: shouldBeConnected = $connectionSwitch !== false;

    $: [colour, text] =
        status === ConnectionStatus.Connected
            ? ["bg-green-500", "connected"]
            : status === ConnectionStatus.Connecting
            ? ["bg-yellow-500", "connecting"]
            : shouldBeConnected
            ? ["bg-red-500", "failed"]
            : ["bg-gray-500", "disconnected"];
</script>

<div class="p-2 flex items-center select-none">
    <div class={`relative w-2 h-2 rounded-full ${colour} transition-colors`}>
        {#if status === ConnectionStatus.Connected}
            <div
                class={`absolute inset-0 rounded-full animate-ping ${colour}`}
            />
        {/if}
    </div>
    <span class="ml-2 text-lg font-medium">{text}</span>
</div>
