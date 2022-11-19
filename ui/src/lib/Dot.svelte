<script lang="ts">
    import { classes, type Vector2 } from "./utils";

    export let r: Vector2;
    export let size: Vector2;

    export let ping = false;

    let className: string | undefined = undefined;
    export { className as class };

    $: transform = `translate(${r.x * size.x}px, ${r.y * size.y}px)`;
</script>

<div
    class={classes("absolute -top-2 -left-2 w-4 h-4 rounded-full", className)}
    style:transform
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
