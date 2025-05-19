namespace PantryPal.API.Models
{
    public class Recipe
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = default!;
        public string Instructions { get; set; } = default!;
        public ICollection<Ingredient> Ingredients { get; set; } = new List<Ingredient>();
        public DateTime CreatedAt { get; set; }
    }
}
