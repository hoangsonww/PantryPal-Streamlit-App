using Microsoft.AspNetCore.Mvc;
using PantryPal.API.Models;
using PantryPal.API.Services;

namespace PantryPal.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RecipesController : ControllerBase
    {
        private readonly IRecipeService _svc;
        public RecipesController(IRecipeService svc) => _svc = svc;

        [HttpPost("generate")]
        public async Task<IActionResult> Generate([FromBody] string[] pantry,
                                                  [FromQuery] string[]? prefs)
        {
            var r = await _svc.GenerateAsync(pantry, prefs);
            return CreatedAtAction(nameof(GetById), new { id = r.Id }, r);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(Guid id) =>
            (await _svc.GetHistoryAsync())
              .FirstOrDefault(r => r.Id == id) is Recipe r
                ? Ok(r)
                : NotFound();

        [HttpGet("history")]
        public async Task<IActionResult> History() =>
            Ok(await _svc.GetHistoryAsync());
    }
}
