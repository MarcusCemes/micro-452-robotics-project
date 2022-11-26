<script lang="ts">
    import { scale } from "$lib/stores";
    import type { Vec2 } from "$lib/utils";

    export let position: Vec2;
    export let orientation: number;

    $: screenPosition = position.toScreenSpace($scale);
</script>

<svg
    class="absolute w-6 h-6"
    viewBox="0 0 64 64"
    xmlns="http://www.w3.org/2000/svg"
    style:--translate-x={`${screenPosition.x}px`}
    style:--translate-y={`${screenPosition.y}px`}
    style:--rotate={`${orientation}rad`}
>
    <path
        d="M 0 64 V 32 A 32 32 0 0 1 32 0 A 32 32 0 0 1 64 32 V 64 64 Z"
        fill="#ddd"
        stroke="#000"
    />
</svg>

<style>
    svg {
        transform: translateX(calc(var(--translate-x) - 50%))
            translateY(calc(var(--translate-y) - 50%))
            rotate(calc(90deg - var(--rotate)));
    }
</style>
