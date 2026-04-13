const ProductCard = ({ product }) => {
  return (
    <div style={{ border: "2px solid #ccc", padding: 35, width: 250,display:'grid', margin: 20,objectFit:'cover',backgroundColor :'#f9f9f9' }}>
      <img src={product.image} width="100%" />
      <h4>{product.name}</h4>
      <p>{product.price}</p>
      <p>{product.description}</p>
      <button onClick={() => console.log(product.name)}>
        Add to Cart
      </button>
    </div>
  );
};

export default ProductCard;