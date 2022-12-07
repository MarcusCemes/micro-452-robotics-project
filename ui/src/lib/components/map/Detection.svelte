<script lang="ts">
    import { Vec2 } from "$lib/utils";
    import type { Scale } from "$lib/stores";

    export let position: Vec2;
    export let orientation: number;
    export let scale: Scale;

    let posScr = position.toScreenSpace(scale);
</script>

<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="-400 0 800 100"
    style:--orientation={`${-orientation}rad`}
    style:--translateX={`${posScr.x}px`}
    style:--translateY={`${posScr.y}px`}
    class="w-12"
>
    <defs>
        <marker
            id="arrowhead"
            markerWidth="12"
            markerHeight="8"
            refX="0"
            refY="3.5"
            orient="auto"
        >
            <polygon points="0 0, 10 3.5, 0 7" />
        </marker>
    </defs>
    <line
        x1="0"
        y1="50"
        x2="250"
        y2="50"
        stroke="#000"
        stroke-width="1rem"
        marker-end="url(#arrowhead)"
    />
</svg>

<style>
    svg {
        transform: translate(
                calc(var(--translateX) - 50%),
                calc(var(--translateY) - 50%)
            )
            rotate(var(--orientation));
    }
</style>
