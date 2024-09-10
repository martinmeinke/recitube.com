<script>
  import {onMount, afterUpdate} from "svelte";
  import IngredientItem from "./IngredientItem.svelte";

  let items = {recipes: []};
  let isLoading = false;
  let error = null;
  let videoId = null;
  let showEmbed = false;
  let previousLink = "";
  let abortController = null;

  export let youtubeLink = "";

  $: {
    if (youtubeLink !== previousLink) {
      videoId = extractVideoId(youtubeLink);
      items = {recipes: []};
      showEmbed = false;
      previousLink = youtubeLink;

      // interrupt the fetchRecipes function
      if (isLoading) {
        // Cancel the ongoing fetch request if there is one
        if (abortController) {
          abortController.abort();
          isLoading = false;
        }
      }
    }
  }

  function extractVideoId(url) {
    const regExp =
      /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
  }

  async function fetchRecipes() {
    if (!videoId) {
      error = "Invalid YouTube URL";
      return;
    }

    // Cancel any ongoing fetch request
    if (abortController) {
      abortController.abort();
    }

    // Create a new AbortController for this fetch request
    abortController = new AbortController();
    const signal = abortController.signal;

    isLoading = true;
    error = null;

    try {
      const response = await fetch(
        `https://2yij6fmwj36dgqss7w7ewy5dhu0czmpd.lambda-url.us-east-1.on.aws/extract-ingredients/?video=${videoId}`,
        {signal},
      );
      if (!response.ok) {
        throw new Error("Failed to fetch recipes");
      }
      items = await response.json();
    } catch (err) {
      if (err.name === "AbortError") {
        console.log("Fetch aborted");
      } else {
        error = err.message;
      }
    } finally {
      isLoading = false;
      abortController = null;
    }
  }

  export function triggerFetch() {
    fetchRecipes();
  }

  function toggleEmbed() {
    showEmbed = !showEmbed;
  }
</script>

<div class="container">
  <div class="input-group">
    <input
      type="text"
      bind:value={youtubeLink}
      placeholder="Enter YouTube URL"
    />
    <button on:click={fetchRecipes} disabled={isLoading}>
      {isLoading ? "Loading..." : "Get Recipes"}
    </button>
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if videoId}
    <div class="video-preview">
      <img
        src="https://img.youtube.com/vi/{videoId}/0.jpg"
        alt="Video thumbnail"
        class="thumbnail"
      />
      <button class="embed-toggle" on:click={toggleEmbed}>
        {showEmbed ? "Hide" : "Show"} Video
      </button>
    </div>
    {#if showEmbed}
      <div class="video-embed">
        <iframe
          width="560"
          height="315"
          src="https://www.youtube.com/embed/{videoId}"
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>
    {/if}
  {/if}

  {#if items.recipes.length > 0}
    <ul class="recipe-list">
      {#each items.recipes as item}
        <li class="recipe-item">
          <h3>{item.name}</h3>
          <ul class="ingredient-list">
            {#each item.ingredients as ingredient}
              <IngredientItem {ingredient} />
            {/each}
          </ul>
        </li>
      {/each}
    </ul>
  {:else if !isLoading && videoId}
    <p>No recipes found for this video.</p>
  {/if}
</div>

<style>
  .container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .input-group {
    display: flex;
    margin-bottom: 20px;
  }

  input {
    flex-grow: 1;
    padding: 10px;
    font-size: 16px;
    border: 1px solid #ccc;
    border-radius: 4px 0 0 4px;
  }

  button {
    padding: 10px 20px;
    font-size: 16px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  button:hover {
    background-color: #45a049;
  }

  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .error {
    color: red;
    margin-bottom: 20px;
  }

  .video-preview {
    margin-bottom: 20px;
    text-align: center;
  }

  .thumbnail {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
  }

  .embed-toggle {
    margin-top: 10px;
    background-color: #2196f3;
    border-radius: 4px;
  }

  .embed-toggle:hover {
    background-color: #0b7dda;
  }

  .video-embed {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
    margin-bottom: 20px;
  }

  .video-embed iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }

  .recipe-list {
    list-style-type: none;
    padding: 0;
  }

  .recipe-item {
    background-color: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    margin-bottom: 20px;
    padding: 15px;
  }

  .recipe-item h3 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #333;
  }

  .ingredient-list {
    list-style-type: none;
    padding-left: 0;
  }

  /* Remove the .ingredient-item style as it's now in IngredientItem.svelte */
</style>
