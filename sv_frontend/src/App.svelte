<script>
  import ItemList from "./ItemList.svelte";

  let itemListComponent;
  let youtubeLink = "";

  // Add an array of preconfigured recipes
  const recipes = [
    {
      name: "Mushroom Pasta",
      url: "https://www.youtube.com/watch?v=6UMM_0NLVEk&t=412s&ab_channel=YeungManCooking",
    },
    {
      name: "Chickpea Curry",
      url: "https://www.youtube.com/watch?v=wF1WCnV5Cyc&ab_channel=AndrewBernard%7CTheNardDogCooks",
    },
    {
      name: "Firecracker Beef",
      url: "https://www.youtube.com/watch?v=pCaOLQAq9KQ&ab_channel=JoshCortis",
    },
  ];

  function handleRecipeClick(url) {
    youtubeLink = url;
  }
</script>

<main>
  <h1>ReciTube</h1>
  <p>
    Please enter a YouTube URL of a cooking video or choose a preconfigured
    recipe:
  </p>

  <div class="recipe-buttons">
    {#each recipes as recipe}
      <button on:click={() => handleRecipeClick(recipe.url)}
        >{recipe.name}</button
      >
    {/each}
  </div>

  <ItemList bind:this={itemListComponent} bind:youtubeLink />
</main>

<style>
  main {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-size: 4em;
    font-weight: 100;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }

  .recipe-buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 20px;
  }

  button {
    background-color: #ff3e00;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  button:hover {
    background-color: #ff6240;
  }
</style>
