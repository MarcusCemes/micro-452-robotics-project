<script lang="ts">
    import ConnectionIndicator from "$lib/components/ConnectionIndicator.svelte";
    import ConnectionParams from "./ConnectionParams.svelte";
    import State from "./State.svelte";
</script>

<div class="p-8">
    <h1 class="mb-1 text-3xl font-bold">Big Brain &ndash; Thymio Controller</h1>
    <div class="mb-6 text-sm text-gray-500">
        École Polytéchnique Fédérale de Laussane
    </div>

    <ConnectionIndicator />
    <ConnectionParams />
    <State />
</div>
