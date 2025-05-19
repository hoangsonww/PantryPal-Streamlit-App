using PantryPal.API.Models;

namespace PantryPal.API.Repositories
{
    public interface IRecipeRepository
    {
        Task<IEnumerable<Recipe>> GetAllAsync();
        Task<Recipe?> GetByIdAsync(Guid id);
        Task AddAsync(Recipe r);
    }
}
