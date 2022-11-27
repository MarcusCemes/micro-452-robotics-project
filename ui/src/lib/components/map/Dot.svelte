<script lang="ts">
    import { scale } from "$lib/stores";
    import { classes, type Vec2 } from "$lib/utils";

    export let r: Vec2;

    export let ping = false;

    let className: string | undefined = undefined;
    export { className as class };

    $: position = r.toScreenSpace($scale);
</script>

<div
    class={classes(
        "absolute -top-2 -left-2 w-4 h-4 rounded-full transform",
        className
    )}
    style:--tw-translate-x={`${position.x}px`}
    style:--tw-translate-y={`${position.y}px`}
>
    {#if ping}
        <div
            class={classes(
                "absolute inset-0 rounded-full animate-ping",
                className
            )}
        />
    {/if}
</div>
