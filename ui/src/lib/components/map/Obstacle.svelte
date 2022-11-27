<script lang="ts">
    import { scale } from "$lib/stores";
    import type { Vec2 } from "$lib/utils";

    export let from: Vec2;
    export let to: Vec2;

    $: position = from.toScreenSpace($scale);
    $: size = to.sub(from).toScreenSpace($scale);
</script>

<div
    class="absolute bg-black"
    style={`left: ${position.x}px; top: ${position.y}px; width: ${size.x}px; height: ${size.y}px;`}
/>
