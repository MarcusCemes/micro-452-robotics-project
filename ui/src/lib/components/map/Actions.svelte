<script lang="ts">
    import { createEventDispatcher } from "svelte";

    import IconButton from "./IconButton.svelte";

    const dispatch = createEventDispatcher();

    export let action: string | null = null;
    export let drawNodes: boolean;
    export let optimise: boolean;

    function setAction(newAction: string) {
        action = newAction;
    }

    function toggleNodes() {
        drawNodes = !drawNodes;
    }

    function toggleOptimise() {
        dispatch("optimise", !optimise);
    }

    function clear() {
        dispatch("clear");
    }

    function onDebug() {
        dispatch("debug");
    }

    function stop() {
        dispatch("stop");
    }
</script>

<div class="mb-2 flex items-center gap-x-1 select-none">
    <IconButton
        on:click={() => setAction("position")}
        active={action === "position"}
    >
        <span class="w-2 h-2 bg-gray-500" />
    </IconButton>
    <IconButton on:click={() => setAction("end")} active={action === "end"}>
        <span class="w-2 h-2 rounded-full bg-red-500" />
    </IconButton>

    <IconButton
        on:click={() => setAction("obstacle")}
        active={action === "obstacle"}
    >
        <span class="w-2 h-2 bg-black" />
    </IconButton>

    <IconButton on:click={clear}>🗑️</IconButton>

    <IconButton on:click={toggleNodes} active={drawNodes}>
        <span class="w-2 h-2 rounded-full bg-orange-500" />
    </IconButton>

    <IconButton on:click={toggleOptimise} active={optimise}>🧭</IconButton>

    <IconButton on:click={onDebug}>🐛</IconButton>

    <IconButton on:click={stop}>⛔</IconButton>
</div>
