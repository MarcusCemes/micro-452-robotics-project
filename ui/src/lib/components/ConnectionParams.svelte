<script lang="ts">
    import {
        connect,
        connectionSwitch,
        disconnect,
        socketUrl,
    } from "$lib/connection";

    $: status = $connectionSwitch;

    $: buttonText = status ? "Disconnect" : "Connect";

    function onClick() {
        if (status) {
            disconnect();
        } else {
            connect();
        }
    }
</script>

<div class="flex items-center">
    <input
        bind:value={$socketUrl}
        class="mr-2 px-2 py-1 border rounded"
        disabled={!!status}
    />

    <button
        on:click={onClick}
        class={`px-2 py-1 border rounded text-white transition-colors duration-100 font-semibold ${
            status
                ? "bg-white text-black hover:bg-gray-100"
                : "bg-blue-500 hover:bg-blue-400 active:bg-blue-600"
        }`}
    >
        {buttonText}
    </button>
</div>
