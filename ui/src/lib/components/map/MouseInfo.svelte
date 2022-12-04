<script lang="ts">
    import type { Scale } from "$lib/stores";
    import { Vec2 } from "$lib/utils";
    import MouseInfoRow from "./MouseInfoRow.svelte";

    export let mousePosition: Vec2 | null;
    export let scale: Scale;
    export let subdivisions: number;

    $: physicalPosition = mousePosition?.toPhysicalSpace(scale);
    $: coordinatePosition = toCoords(physicalPosition);

    function toCoords(position?: Vec2) {
        if (!position) return;
        const r = position.multiply(subdivisions).divide(scale.physicalSize);
        return new Vec2(Math.floor(r.x), Math.floor(r.y));
    }
</script>

<div class="mt-2 grid grid-cols-[repeat(3,auto)] gap-x-2 text-sm">
    <MouseInfoRow value={mousePosition}>Cursor [px]</MouseInfoRow>
    <MouseInfoRow value={physicalPosition}>Position [cm]</MouseInfoRow>
    <MouseInfoRow value={coordinatePosition} decimals={0}>
        Coordinates
    </MouseInfoRow>
</div>
