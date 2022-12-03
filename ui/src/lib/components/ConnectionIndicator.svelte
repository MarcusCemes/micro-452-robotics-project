<script lang="ts">
    import {
        ConnectionStatus,
        connectionStatus,
        connectionSwitch,
    } from "$lib/connection";

    $: status = $connectionStatus;

    $: pulse = [
        ConnectionStatus.Connecting,
        ConnectionStatus.Connected,
    ].includes(status);

    $: shouldBeConnected = $connectionSwitch !== false;

    $: [colour, text] =
        status === ConnectionStatus.Connected
            ? ["bg-green-500", "Connected"]
            : status === ConnectionStatus.Connecting
            ? ["bg-yellow-500", "Connecting"]
            : shouldBeConnected
            ? ["bg-red-500", "Failed"]
            : ["bg-gray-500", "Disconnected"];
</script>

<div class="mb-4 flex justify-center items-center select-none">
    <div class={`relative w-2 h-2 rounded-full ${colour} transition-colors`}>
        {#if pulse}
            <div
                class={`absolute inset-0 rounded-full animate-ping ${colour}`}
            />
        {/if}
    </div>
    <span class="ml-2 font-medium">{text}</span>
</div>
