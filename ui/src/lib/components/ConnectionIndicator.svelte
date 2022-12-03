<script lang="ts">
    import { ConnectionStatus, connectionStatus } from "$lib/connection";
    import { expoInOut } from "svelte/easing";
    import { fly } from "svelte/transition";

    $: status = $connectionStatus;
    $: [colour, text, pulse] = getVariables(status);

    function getVariables(status: ConnectionStatus) {
        switch (status) {
            case ConnectionStatus.Connected:
                return ["bg-green-500", "Connected", true];
            case ConnectionStatus.Connecting:
                return ["bg-yellow-500", "Connecting", true];
            case ConnectionStatus.Failed:
                return ["bg-red-500", "Failed"];
            default:
                return ["bg-gray-500", "Disconnected"];
        }
    }
</script>

<div class="mb-3 flex justify-center items-center">
    <div
        class={`relative w-2.5 h-2.5 rounded-full ${colour} transition-colors`}
    >
        {#if pulse}
            <div
                class={`absolute inset-0 rounded-full animate-ping ${colour}`}
            />
        {/if}
    </div>

    <div class="relative ml-2 w-12 h-6 font-semibold">
        {#key text}
            <div
                in:fly={{ x: 10, duration: 800, easing: expoInOut }}
                out:fly={{ x: -10, duration: 800, easing: expoInOut }}
                class="absolute top-0 left-0 h-full"
            >
                {text}
            </div>
        {/key}
    </div>
</div>
