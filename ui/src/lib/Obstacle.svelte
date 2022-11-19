<script lang="ts">
    import { app } from "./stores";
    import type { Vec2 } from "./utils";

    export let from: Vec2;
    export let to: Vec2;

    $: position = from.toScreenSpace($app);
    $: size = to.sub(from).toScreenSpace($app);
</script>

<div
    class="absolute bg-black"
    style={`left: ${position.x}px; top: ${position.y}px; width: ${size.x}px; height: ${size.y}px;`}
/>
