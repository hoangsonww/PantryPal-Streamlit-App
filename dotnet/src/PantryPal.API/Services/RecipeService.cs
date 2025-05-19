using PantryPal.API.Models;
using PantryPal.API.Repositories;

namespace PantryPal.API.Services
{
    public class RecipeService : IRecipeService
    {
        private readonly IRecipeRepository _repo;
        public RecipeService(IRecipeRepository repo) => _repo = repo;

        public async Task<Recipe> GenerateAsync(IEnumerable<string> pantry, IEnumerable<string>? prefs)
        {
            // stub: integrate Gemini AI here
            var recipe = new Recipe {
                Id = Guid.NewGuid(),
                Title = "Sample AI Recipe",
                Instructions = "1. Mix ingredients.\n2. Cook.\n3. Serve.",
                CreatedAt = DateTime.UtcNow
            };
            foreach(var i in pantry) recipe.Ingredients.Add(new Ingredient { Id = Guid.NewGuid(), Name = i });
            await _repo.AddAsync(recipe);
            return recipe;
        }

        public Task<IEnumerable<Recipe>> GetHistoryAsync() =>
            _repo.GetAllAsync();
    }
}
