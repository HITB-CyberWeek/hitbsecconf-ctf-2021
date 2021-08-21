using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace svghost.utils
{
	public sealed class ReadSafeLinkedListNode<T>
	{
		public class LinkedList : IEnumerable<T>
		{
			public LinkedList()
			{
				head = new ReadSafeLinkedListNode<T>(default);
				head.prev = head;
				head.next = head;
			}

			public int Count => count;

			public ReadSafeLinkedListNode<T> First
			{
				get
				{
					var node = head.next;
					return node == head ? null : node;
				}
			}

			public ReadSafeLinkedListNode<T> Last
			{
				get
				{
					var node = head.prev;
					return node == head ? null : node;
				}
			}

			public ReadSafeLinkedListNode<T> AddFirst(T value)
			{
				var result = new ReadSafeLinkedListNode<T>(value);
				InsertNodeBefore(head.next, result);
				return result;
			}

			public ReadSafeLinkedListNode<T> AddLast(T value)
			{
				var result = new ReadSafeLinkedListNode<T>(value);
				InsertNodeBefore(head, result);
				return result;
			}

			public void RemoveFirst()
			{
				if(head == head.next)
					throw new InvalidOperationException("List is empty");

				RemoveNode(head.next);
			}

			public void RemoveLast()
			{
				if(head == head.prev)
					throw new InvalidOperationException("List is empty");

				RemoveNode(head.prev);
			}

			private void InsertNodeBefore(ReadSafeLinkedListNode<T> node, ReadSafeLinkedListNode<T> newNode)
			{
				newNode.next = node;
				newNode.prev = node.prev;
				Thread.MemoryBarrier();
				node.prev.next = newNode;
				node.prev = newNode;
				count++;
			}

			private void RemoveNode(ReadSafeLinkedListNode<T> node)
			{
				node.next.prev = node.prev;
				node.prev.next = node.next;
				count--;
			}

			public ReadSafeLinkedListEnumerator GetEnumerator() => new ReadSafeLinkedListEnumerator(this);

			IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
			IEnumerator<T> IEnumerable<T>.GetEnumerator() => GetEnumerator();

			public struct ReadSafeLinkedListEnumerator : IEnumerator<T>
			{
				internal ReadSafeLinkedListEnumerator(LinkedList list)
				{
					this.list = list;
					node = list.head;
					value = default;
				}

				public T Current => node != list.head ? value : throw new InvalidOperationException("Enumeration not started");
				object IEnumerator.Current => Current;

				public bool MoveNext()
				{
					node = node.next;
					if(node == list.head)
						return false;
					value = node.item;
					return true;
				}

				void IEnumerator.Reset()
				{
					value = default;
					node = list.head;
				}

				public void Dispose() {}

				private readonly LinkedList list;
				private ReadSafeLinkedListNode<T> node;
				private T value;
			}

			private readonly ReadSafeLinkedListNode<T> head;
			private int count;
		}

		private ReadSafeLinkedListNode(T value) => item = value;

		public T Value
		{
			get => item;
			set => item = value;
		}

		private ReadSafeLinkedListNode<T> next, prev;
		private T item;
	}
}
