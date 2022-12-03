<script lang="ts">
    import {
        ConnectionStatus,
        connectionStatus,
        disconnect,
        reconnect,
        socketUrl,
    } from "$lib/connection";

    $: status = $connectionStatus;
    $: connected = status === ConnectionStatus.Connected;
    $: buttonText = connected ? "Disconnect" : "Connect";

    $: disabled = [
        ConnectionStatus.Connecting,
        ConnectionStatus.Connected,
    ].includes(status);

    function onClick() {
        if (connected) disconnect();
        else reconnect();
    }
</script>

<div class="flex justify-center items-center">
    <input
        bind:value={$socketUrl}
        class="mr-2 px-2 py-1 border rounded"
        {disabled}
    />

    <button
        on:click={onClick}
        class={`px-2 py-1 border rounded text-white transition-colors duration-100 font-semibold disabled:bg-gray-300 disabled:text-gray-500 ${
            connected
                ? "bg-white text-black hover:bg-gray-100"
                : "bg-blue-500 hover:bg-blue-400 active:bg-blue-600"
        }`}
        disabled={status === ConnectionStatus.Connecting}
    >
        {buttonText}
    </button>
</div>
