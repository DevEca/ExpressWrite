-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 03, 2022 at 08:20 AM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `expresswrite`
--

-- --------------------------------------------------------

--
-- Table structure for table `result_table`
--

CREATE TABLE `result_table` (
  `result_id` int(100) NOT NULL,
  `result_text` text NOT NULL,
  `user_id` int(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `result_table`
--

INSERT INTO `result_table` (`result_id`, `result_text`, `user_id`) VALUES
(1, '         \n         Dear Mrs Miller Ray is so sick he cannot go to school . Rays Mom\n         \n      ', 10),
(2, '         \n         This is the first line of this text example . This is the second line of the same text .\n         \n      ', 10),
(3, '         \r\n         Do something today that your future self will thank you for .\r\n         \r\n      ', 10),
(4, '         \r\n         FOX THE QUICK BROWN JUMPS OVER THE LAZY DOG . WAIT ... THERE\'S A FOX IN THE HOUSE ?\r\n         \r\n      ', 10),
(5, '         \r\n         I have a little dog Cailed prince lelsbrow hand Cydly Hellises tos le epailday .\r\n         \r\n      ', 10),
(6, '         \r\n         This is the first line of this text example . This is the second line of the same text .\r\n         \r\n      ', 10),
(7, '         \r\n         FOX THE QUICK BROWN JUMPS OVER THE LAZY DOG . WAIT ... THERE\'S A FOX IN THE HOUSE ?\r\n         \r\n      ', 11),
(8, '         \r\n         FOX THE QUICK BROWN JUMPS OVER THE LAZY DOG . WAIT ... THERE\'S A FOX IN THE HOUSE ?\r\n         \r\n      ', 9),
(9, '         \r\n         Do something today that your future self will thank you for .\r\n         \r\n      ', 9),
(10, '         \r\n       NA JAEMIN  Do something today that your future self will thank you for . \r\n         \r\n      ', 9),
(11, '         \r\n        JENO: This is the first line of this text example . This is the second line of the same text .\r\n         \r\n      ', 12),
(12, '         \r\n        This is the first line of this text example . This is the second line of the same text .\r\n         \r\n      ', 12),
(13, 'This is the first line of this text example. This is the second line of the same text.', 12),
(14, '         \r\n         Do something today that your future self will thank you for .\r\n         \r\n      ', 10),
(15, '         \n         FOX THE QUICK BROWN JUMPS OVER THE LAZY DOG . WAIT ... THERE\'S A FOX IN THE HOUSE ?\n         \n      ', 10);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `password`) VALUES
(1, 'shannon', 'shanndel25@gmail.com', '123456'),
(2, 'Shann Del Rosario', 'shanndel25@gmail.com', '111111'),
(3, 'Erica Orpiano', 'ericaorpiano1327@gmail.com', 'jaemin'),
(5, 'Erica Orpiano', 'ericaorpiano1327@gmail.com', 'nana'),
(6, 'jenelle', 'jenellebarachina@gmail.com', 'nelji'),
(7, 'Erica Orpiano', 'chanplusyeol@gmail.com', 'marklee'),
(8, 'Na Jaemin', 'najaemin@gmail.com', 'najaemin'),
(9, 'Mark Lee', 'marklee@gmail.com', '0202'),
(10, 'eorpiano', 'eca@gmail.com', 'eca'),
(11, 'njm0813', 'najaemin0813@gmail.com', 'nana0813'),
(12, 'leejeno', 'ljn@gmail.com', 'onej'),
(13, 'pjsung', 'parkjisung@gmail', '123'),
(14, 'pjsung', 'parkjisung@gmail', '123');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `result_table`
--
ALTER TABLE `result_table`
  ADD PRIMARY KEY (`result_id`),
  ADD KEY `result_text` (`user_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `result_table`
--
ALTER TABLE `result_table`
  MODIFY `result_id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `result_table`
--
ALTER TABLE `result_table`
  ADD CONSTRAINT `result_text` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
