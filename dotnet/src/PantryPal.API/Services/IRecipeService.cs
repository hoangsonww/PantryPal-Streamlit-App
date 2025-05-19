using PantryPal.API.Models;

namespace PantryPal.API.Services
{
    public interface IRecipeService
    {
        Task<Recipe> GenerateAsync(IEnumerable<string> pantry, IEnumerable<string>? prefs);
        Task<IEnumerable<Recipe>> GetHistoryAsync();
    }
}
