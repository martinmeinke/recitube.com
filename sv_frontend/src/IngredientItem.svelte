<script>
  export let ingredient;

  function createWalmartSearchUrl(ingredient) {
    return `https://www.walmart.com/search?q=${encodeURIComponent(ingredient)}`;
  }

  function createWholeFoodsSearchUrl(ingredient) {
    return `https://www.amazon.com/s?k=${encodeURIComponent(ingredient)}&i=wholefoods`;
  }
</script>

<li class="ingredient-item">
  <span class="ingredient-name">{ingredient}</span>
  <div class="shopping-links">
    <a
      href={createWalmartSearchUrl(ingredient)}
      target="_blank"
      rel="noopener noreferrer"
      class="walmart-link"
    >
      Walmart
    </a>
    <a
      href={createWholeFoodsSearchUrl(ingredient)}
      target="_blank"
      rel="noopener noreferrer"
      class="whole-foods-link"
    >
      Whole Foods
    </a>
  </div>
</li>

<style>
  .ingredient-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    margin-bottom: 10px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
    transition: background-color 0.3s;
  }

  .ingredient-item:hover {
    background-color: #f0f0f0;
  }

  .ingredient-name {
    font-weight: 500;
  }

  .shopping-links {
    display: flex;
    gap: 10px;
  }

  .shopping-links a {
    font-size: 0.8em;
    text-decoration: none;
    padding: 4px 8px;
    border-radius: 3px;
    transition: opacity 0.3s;
  }

  .shopping-links a:hover {
    opacity: 0.8;
  }

  .walmart-link {
    background-color: #0071ce;
    color: white;
  }

  .whole-foods-link {
    background-color: #ffcc00;
    color: black;
  }
</style>
