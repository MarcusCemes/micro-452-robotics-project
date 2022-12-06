<script lang="ts">
    import type { Scale } from "$lib/stores";
    import type { Vec2 } from "$lib/utils";

    export let position: Vec2;
    export let orientation: number;
    export let scale: Scale;

    $: screenPosition = position.toScreenSpace(scale);
</script>

<svg
    class="absolute w-12 opacity-50 text-cyan-500"
    viewBox="-64 0 128 64"
    xmlns="http://www.w3.org/2000/svg"
    style:--translateX={`${screenPosition.x}px`}
    style:--translateY={`${screenPosition.y}px`}
    style:--rotate={`${-orientation}rad`}
>
    <path
        d="M 0 10 L 0 54 L 64 32 Z"
        fill="currentColor"
    />
</svg>

<style>
    svg {
        transform: translateX(calc(var(--translateX) - 50%))
            translateY(calc(var(--translateY) - 50%))
            rotate(calc(var(--rotate)));
    }
</style>
