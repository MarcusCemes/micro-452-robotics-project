<script lang="ts">
    import { scale } from "$lib/stores";
    import type { Vec2 } from "$lib/utils";

    export let from: Vec2;
    export let to: Vec2;
    export let screenSpace = false;

    $: styles = calculateStyles(from, to, screenSpace);

    function calculateStyles(from: Vec2, to: Vec2, screenSpace: boolean) {
        if (!screenSpace) {
            from = from.toScreenSpace($scale);
            to = to.toScreenSpace($scale);
        }

        return {
            top: `${Math.min(to.y, from.y)}px`,
            left: `${Math.min(from.x, to.x)}px`,
            width: `${Math.abs(to.x - from.x)}px`,
            height: `${Math.abs(from.y - to.y)}px`,
        };
    }
</script>

<div
    class="absolute bg-black"
    style:top={styles.top}
    style:left={styles.left}
    style:width={styles.width}
    style:height={styles.height}
/>
