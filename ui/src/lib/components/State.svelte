<script lang="ts">
    import { state } from "$lib/connection";

    $: stateText = JSON.stringify(filter($state.state), null, 2);

    function filter(state: any) {
        const newState = { ...state };

        for (const key of ["path", "obstacles"]) {
            if (key in newState) {
                newState[key] = "<filtered>";
            }
        }

        return newState;
    }
</script>

<h2 class="mb-2 text-xl font-bold">State</h2>
<pre
    class="p-2 bg-gray-100 rounded font-mono overflow-x-auto text-sm">{stateText}</pre>
