<script lang="ts">
    import { app } from "./stores";
    import { classes, px, type Vec2 } from "./utils";

    export let r: Vec2;

    export let ping = false;

    let className: string | undefined = undefined;
    export { className as class };

    $: position = r.toScreenSpace($app);
</script>

<div
    class={classes(
        "absolute -top-2 -left-2 w-4 h-4 rounded-full transform",
        className
    )}
    style:--tw-translate-x={px(position.x)}
    style:--tw-translate-y={px(position.y)}
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
