import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Star, ShoppingCart } from 'lucide-react';
import axiosInstance from '../../services/api';
import toast from 'react-hot-toast';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    fetchProductDetail();
  }, [id]);

  const fetchProductDetail = async () => {
    try {
      const response = await axiosInstance.get(`/products/${id}`);
      setProduct(response.data.data);
    } catch (error) {
      toast.error('Failed to load product');
      navigate('/products');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (quantity > product.stock) {
      toast.error('Insufficient stock');
      return;
    }
    toast.success(`${quantity} items added to cart`);
    // TODO: Implement cart functionality
  };

  const handleAddReview = async () => {
    if (!comment.trim()) {
      toast.error('Please enter a comment');
      return;
    }

    setReviewLoading(true);
    try {
      await axiosInstance.post('/reviews', {
        product_id: id,
        rating,
        comment,
      });
      toast.success('Review posted successfully');
      setComment('');
      setRating(5);
      fetchProductDetail();
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to post review');
    } finally {
      setReviewLoading(false);
    }
  };

  if (loading) return <div className="container mx-auto px-4 py-8">Loading...</div>;
  if (!product) return <div className="container mx-auto px-4 py-8">Product not found</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Product Images */}
        <div>
          {product.images.length > 0 ? (
            <img
              src={product.images[0].url}
              alt={product.name}
              className="w-full rounded-lg"
            />
          ) : (
            <div className="w-full h-96 bg-gray-200 rounded-lg"></div>
          )}
          {product.images.length > 1 && (
            <div className="flex gap-2 mt-4">
              {product.images.map((img) => (
                <img
                  key={img.id}
                  src={img.url}
                  alt=""
                  className="w-20 h-20 object-cover rounded cursor-pointer hover:opacity-75"
                />
              ))}
            </div>
          )}
        </div>

        {/* Product Details */}
        <div>
          <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
          
          <div className="flex items-center gap-4 mb-6">
            <span className="text-3xl font-bold text-blue-600">${product.price.toFixed(2)}</span>
            <div className="flex items-center">
              <Star className="text-yellow-500" size={24} />
              <span className="ml-2 text-lg font-semibold">
                {product.average_rating.toFixed(1)} ({product.review_count} reviews)
              </span>
            </div>
          </div>

          <p className="text-gray-600 mb-6">{product.description}</p>

          {/* Stock Status */}
          <div className="mb-6">
            <p className={`text-lg font-semibold ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
            </p>
          </div>

          {/* Sizes */}
          {product.sizes.length > 0 && (
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Size</label>
              <select className="input">
                {product.sizes.map((size) => (
                  <option key={size.id} value={size.size}>
                    {size.size}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Quantity */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Quantity</label>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="btn btn-secondary px-3"
              >
                -
              </button>
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))}
                className="input w-16 text-center"
                min="1"
                max={product.stock}
              />
              <button
                onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
                className="btn btn-secondary px-3"
              >
                +
              </button>
            </div>
          </div>

          {/* Add to Cart & Checkout */}
          <button
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className="btn btn-primary w-full disabled:opacity-50 mb-4 flex items-center justify-center gap-2"
          >
            <ShoppingCart size={20} />
            Add to Cart
          </button>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Add Review Form */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Write a Review</h2>
          <div className="space-y-4">
            <div>
              <label className="label">Rating</label>
              <select
                className="input"
                value={rating}
                onChange={(e) => setRating(Number(e.target.value))}
              >
                <option value={1}>1 - Poor</option>
                <option value={2}>2 - Fair</option>
                <option value={3}>3 - Good</option>
                <option value={4}>4 - Very Good</option>
                <option value={5}>5 - Excellent</option>
              </select>
            </div>

            <div>
              <label className="label">Comment</label>
              <textarea
                className="input"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows="5"
                placeholder="Share your experience with this product..."
              />
            </div>

            <button
              onClick={handleAddReview}
              disabled={reviewLoading}
              className="btn btn-primary w-full disabled:opacity-50"
            >
              {reviewLoading ? 'Posting...' : 'Post Review'}
            </button>
          </div>
        </div>

        {/* Reviews List */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-6">Customer Reviews</h2>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {product.reviews.length === 0 ? (
              <p className="text-gray-600">No reviews yet. Be the first!</p>
            ) : (
              product.reviews.map((review) => (
                <div key={review.id} className="border-b pb-4 last:border-b-0">
                  <div className="flex justify-between items-start mb-2">
                    <strong>{review.user_name}</strong>
                    <span className="text-yellow-500">★ {review.rating}</span>
                  </div>
                  <p className="text-gray-700">{review.comment}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    {new Date(review.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
