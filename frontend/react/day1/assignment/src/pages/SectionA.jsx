import ProfileCard from "../components/ProfileCard";
import Button from "../components/Button";
import ProductCard from "../components/ProductCard";

const SectionA = () => {
  const products = Array.from({ length: 6 }, (_, i) => ({
    id: i,
    name: "Product " + i,
    price: "$" + (i * 10),
    description: "Sample product",
    image: "https://images.pexels.com/photos/32418799/pexels-photo-32418799.jpeg"
  }));

  return (
    <div>
      <h2>Section A</h2>

      {/* Q1 */}
      <ProfileCard name="Rani" title="Software Engineer" bio="Passionate Software Developer skilled in Python, Machine Learning, and Deep Learning. I love building intelligent systems and user-friendly applications that solve real-world problems." avatarUrl="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPMOmm8UQ4JkG4l2uuB-2d6QrITEbn8FaGgHfKu9zQo7djXevfBUoJ2wc&s"/> 
      <ProfileCard name="Rishab" title="Software Engineer" bio="Curious mind with a strong interest in technology and innovation. I enjoy learning new tools, building projects, and turning ideas into impactful digital solutions." avatarUrl="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPMOmm8UQ4JkG4l2uuB-2d6QrITEbn8FaGgHfKu9zQo7djXevfBUoJ2wc&s"/>
      <ProfileCard name="Ram" title="Software Engineer" bio="Data Science enthusiast with hands-on experience in machine learning and computer vision. Focused on transforming data into meaningful insights and smart applications." avatarUrl="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPMOmm8UQ4JkG4l2uuB-2d6QrITEbn8FaGgHfKu9zQo7djXevfBUoJ2wc&s"/>

      {/* Q2 */}
      <Button label="Save" color="green" onClick={() => alert("Saved")} />
      <Button label="Cancel" color="orange" onClick={() => alert("Cancelled")} />
      <Button label="Delete" color="red" onClick={() => alert("Deleted")} />

      {/* Q3 */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)" }}>
        {products.map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </div>
  );
};

export default SectionA;