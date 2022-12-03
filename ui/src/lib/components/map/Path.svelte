<script lang="ts">
    import type { Scale } from "$lib/stores";
    import type { Vec2 } from "$lib/utils";

    export let path: Vec2[];
    export let scale: Scale;

    $: width = scale.mapSize.x;
    $: height = scale.mapSize.y;

    $: points = path
        ?.map((p) => p.toScreenSpace(scale))
        .map(({ x, y }) => `${x} ${y}`)
        .join(",");
</script>

<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox={`0 0 ${width} ${height}`}
    {width}
    {height}
    class="absolute top-0 left-0 text-teal-500"
>
    <polyline
        {points}
        stroke="currentColor"
        fill="none"
        stroke-width="0.2em"
        stroke-linejoin="miter"
    />
</svg>
