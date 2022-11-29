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
    class="max-h-96 p-2 bg-gray-100 rounded font-mono overflow-x-auto overflow-y-auto  text-sm">{stateText}</pre>
