function mytheme_the_date( $date ) {
    $time = strtotime( $date );
    $difference = time() - $time;
    $days_ago = (int)( $difference / 60 / 60 / 24 );
    
    if ( date( 'Y-m-d' ) === date( 'Y-m-d', $time ) )
        return __( 'Today' );
    elseif ( date( 'Y-m-d', strtotime('-1 day') ) === date( 'Y-m-d', $time ) )
        return __( 'Yesterday' );
    elseif ( $days_ago < 7 )
        return sprintf( __( '%d days ago' ), $days_ago );
        return $date;
    }
    add_filter( 'the_date', 'mytheme_the_date' );