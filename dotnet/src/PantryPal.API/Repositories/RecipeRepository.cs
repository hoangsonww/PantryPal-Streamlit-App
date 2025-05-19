using Microsoft.EntityFrameworkCore;
using PantryPal.API.Data;
using PantryPal.API.Models;

namespace PantryPal.API.Repositories
{
    public class RecipeRepository : IRecipeRepository
    {
        private readonly AppDbContext _db;
        public RecipeRepository(AppDbContext db) => _db = db;

        public async Task<IEnumerable<Recipe>> GetAllAsync() =>
            await _db.Recipes.Include(r => r.Ingredients).ToListAsync();

        public async Task<Recipe?> GetByIdAsync(Guid id) =>
            await _db.Recipes.Include(r => r.Ingredients).FirstOrDefaultAsync(r => r.Id == id);

        public async Task AddAsync(Recipe r)
        {
            _db.Recipes.Add(r);
            await _db.SaveChangesAsync();
        }
    }
}
