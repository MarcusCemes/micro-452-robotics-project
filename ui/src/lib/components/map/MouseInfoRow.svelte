<script lang="ts">
    import type { Vec2 } from "$lib/utils";

    const PADDING = 4;

    export let value: Vec2 | null | undefined;
    export let decimals = 2;

    $: [x, y] = (
        value?.array().map((n) => n.toFixed(decimals)) || ["-", "-"]
    ).map((n) => n.padStart(PADDING));
</script>

<div class="font-bold"><slot /></div>
<div class="w-24">{x}</div>
<div class="w-24">{y}</div>
