<script lang="ts">
    import { scale } from "$lib/stores";
    import { classes, type Vec2 } from "$lib/utils";

    export let ping = false;
    export let position: Vec2;
    export let small = false;

    let className: string | undefined = undefined;
    export { className as class };

    $: screenPosition = position.toScreenSpace($scale);
</script>

<div
    class={classes(
        "absolute rounded-full transform",
        small ? "w-2 h-2 -top-1 -left-1" : "w-4 h-4 -top-2 -left-2",
        className
    )}
    style:--tw-translate-x={`${screenPosition.x}px`}
    style:--tw-translate-y={`${screenPosition.y}px`}
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
